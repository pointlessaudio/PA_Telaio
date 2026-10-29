/*
 * PA-TELAIO — firmware di collaudo per il prototipo veroboard
 * Daisy Seed3, 2x TLC2272 (DIP-8), stereo in/out.
 *
 * Cosa fa:
 *  - passthrough stereo con inversione di fase (lo stadio d'uscita hardware è invertente)
 *  - K1 (D0): bypass on/off, LED (D9) acceso = effetto attivo
 *  - K2 (D10): modo mono (IN L duplicato su entrambe le uscite)
 *    Il jack "pedale" sul retro è in parallelo ai tasti: punta = K1, anello = K2.
 *  - K1 + K2 tenuti premuti all'accensione: bootloader STM32 per il flash via USB
 *    (make program-dfu) senza aprire il case
 *  - Pot 1 (A0): volume 0..2x quando l'effetto è attivo
 *  - Pot 1-6 (A0-A5): valori a display
 *  - Encoder (A=D3, B=D7, SW=D8): contatore e pulsante a display;
 *    ogni pressione manda un Do centrale su MIDI OUT
 *  - MIDI IN/OUT su USART1 (TX=D13, RX=D14): ultima nota o CC ricevuti a display
 *  - OLED SSD1306/SSD1309 I2C sui pin di default di libDaisy (SCL=D11, SDA=D12)
 *  - picchi d'ingresso L/R in dBFS e versione della scheda rilevata
 *
 * Mappa pin: vedi hardware/layout.py e CLAUDE.md. Non cambiarla senza aggiornare il layout.
 */
#include "daisy_seed.h"
#include "dev/oled_ssd130x.h"
#include <cmath>
#include <cstdio>

using namespace daisy;

using Oled = OledDisplay<SSD130xI2c128x64Driver>;

static DaisySeed       hw;
static Oled            display;
static Encoder         encoder;
static Switch          k1, k2;
static GPIO            led;
static MidiUartHandler midi;

// Stato condiviso tra callback audio e loop principale
static volatile bool  bypass    = true;
static volatile bool  mono      = false;
static volatile float gain      = 1.0f;
static volatile float peak_l    = 0.0f;
static volatile float peak_r    = 0.0f;

static constexpr int kNumPots = 6;

static void AudioCallback(AudioHandle::InputBuffer  in,
                          AudioHandle::OutputBuffer out,
                          size_t                    size)
{
    const float g  = bypass ? 1.0f : gain;
    float       pl = peak_l;
    float       pr = peak_r;
    for(size_t i = 0; i < size; i++)
    {
        const float l = in[0][i];
        const float r = mono ? l : in[1][i];
        pl = fmaxf(pl, fabsf(l));
        pr = fmaxf(pr, fabsf(in[1][i]));
        // Inversione di fase: compensa lo stadio d'uscita invertente (U2)
        out[0][i] = -l * g;
        out[1][i] = -r * g;
    }
    peak_l = pl;
    peak_r = pr;
}

static const char* BoardName(DaisySeed::BoardVersion v)
{
    switch(v)
    {
        case DaisySeed::BoardVersion::DAISY_SEED_3: return "Seed3";
        case DaisySeed::BoardVersion::DAISY_SEED_1_2: return "Seed 1.2";
        case DaisySeed::BoardVersion::DAISY_SEED_2_DFM: return "Seed2 DFM";
        case DaisySeed::BoardVersion::DAISY_SEED_1_1: return "Seed 1.1";
        default: return "Seed rev4";
    }
}

static int ToDb(float peak)
{
    if(peak < 1e-5f)
        return -99;
    return static_cast<int>(20.0f * log10f(peak));
}

int main(void)
{
    hw.Init(true); // 480 MHz
    hw.SetAudioBlockSize(48);
    // 48 kHz di default. Per provare 96 o 192 kHz sul Seed3 cambiare qui
    // e verificare a banco: vedi CLAUDE.md, sezione "Da verificare".
    hw.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);

    // Pot 1-6 su A0-A5
    AdcChannelConfig adc_cfg[kNumPots];
    const Pin        pot_pins[kNumPots]
        = {seed::A0, seed::A1, seed::A2, seed::A3, seed::A4, seed::A5};
    for(int i = 0; i < kNumPots; i++)
        adc_cfg[i].InitSingle(pot_pins[i]);
    hw.adc.Init(adc_cfg, kNumPots);
    hw.adc.Start();

    // Controlli: pull-up interni, chiudono verso massa
    encoder.Init(seed::D3, seed::D7, seed::D8);
    k1.Init(seed::D0);
    k2.Init(seed::D10);
    led.Init(seed::D9, GPIO::Mode::OUTPUT);

    // OLED su I2C1, pin di default di libDaisy (SCL = D11, SDA = D12).
    // 400 kHz invece del default 1 MHz: i cavi arrivano fino al pannello.
    Oled::Config disp_cfg;
    disp_cfg.driver_config.transport_config.i2c_config.speed
        = I2CHandle::Config::Speed::I2C_400KHZ;
    display.Init(disp_cfg);

    // K1 + K2 premuti all'accensione: bootloader STM32, flash via USB-C
    // con il case chiuso (BOOT e RESET del Seed restano dentro).
    for(int i = 0; i < 50; i++)
    {
        k1.Debounce();
        k2.Debounce();
        System::Delay(1);
    }
    if(k1.Pressed() && k2.Pressed())
    {
        display.Fill(false);
        display.SetCursor(0, 28);
        display.WriteString("DFU: flash via USB", Font_6x8, true);
        display.Update();
        System::ResetToBootloader(System::BootloaderMode::STM);
    }

    // MIDI su USART1 (TX = D13, RX = D14), come nei DevKit ufficiali Seed3
    MidiUartHandler::Config midi_cfg;
    midi_cfg.transport_config.periph = UartHandler::Config::Peripheral::USART_1;
    midi_cfg.transport_config.rx     = seed::D14;
    midi_cfg.transport_config.tx     = seed::D13;
    midi.Init(midi_cfg);
    midi.StartReceive();

    const char* board = BoardName(hw.CheckBoardVersion());

    hw.StartAudio(AudioCallback);

    int      enc_count  = 0;
    uint32_t last_draw  = 0;
    char     line[32];
    char     midi_str[16] = "--";

    for(;;)
    {
        // Controlli a ~1 kHz
        encoder.Debounce();
        k1.Debounce();
        k2.Debounce();
        enc_count += encoder.Increment();
        if(k1.RisingEdge())
            bypass = !bypass;
        if(k2.RisingEdge())
            mono = !mono;
        led.Write(!bypass);
        gain = hw.adc.GetFloat(0) * 2.0f;

        // MIDI OUT: il pulsante dell'encoder suona un Do centrale sul canale 1
        if(encoder.RisingEdge())
        {
            uint8_t note_on[3] = {0x90, 60, 100};
            midi.SendMessage(note_on, 3);
        }
        if(encoder.FallingEdge())
        {
            uint8_t note_off[3] = {0x80, 60, 0};
            midi.SendMessage(note_off, 3);
        }

        // MIDI IN: tiene l'ultima nota o CC ricevuti
        midi.Listen();
        while(midi.HasEvents())
        {
            MidiEvent ev = midi.PopEvent();
            if(ev.type == NoteOn)
                snprintf(midi_str, sizeof(midi_str), "n%d v%d", ev.data[0], ev.data[1]);
            else if(ev.type == ControlChange)
                snprintf(midi_str, sizeof(midi_str), "c%d v%d", ev.data[0], ev.data[1]);
        }

        const uint32_t now = System::GetNow();
        if(now - last_draw >= 50)
        {
            last_draw = now;
            display.Fill(false);

            snprintf(line, sizeof(line), "%s %s %s", board,
                     bypass ? "BYP" : "ON ", mono ? "MONO" : "ST");
            display.SetCursor(0, 0);
            display.WriteString(line, Font_6x8, true);

            snprintf(line, sizeof(line), "IN L %3d  R %3d dB", ToDb(peak_l), ToDb(peak_r));
            display.SetCursor(0, 10);
            display.WriteString(line, Font_6x8, true);
            // decadimento dei picchi
            peak_l = peak_l * 0.8f;
            peak_r = peak_r * 0.8f;

            // barre dei sei pot
            for(int i = 0; i < kNumPots; i++)
            {
                const int y = 20 + i * 6;
                const int w = static_cast<int>(hw.adc.GetFloat(i) * 100.0f);
                snprintf(line, sizeof(line), "%d", i + 1);
                display.SetCursor(0, y);
                display.WriteString(line, Font_6x8, true);
                display.DrawRect(10, y + 1, 10 + 100, y + 4, true, false);
                if(w > 0)
                    display.DrawRect(10, y + 1, 10 + w, y + 4, true, true);
            }

            // encoder (* = premuto) e ultimo messaggio MIDI ricevuto
            snprintf(line, sizeof(line), "E%+d%s  M %s", enc_count,
                     encoder.Pressed() ? "*" : " ", midi_str);
            display.SetCursor(0, 56);
            display.WriteString(line, Font_6x8, true);

            display.Update();
        }
        System::Delay(1);
    }
}
