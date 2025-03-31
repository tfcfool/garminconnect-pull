# garminconnect-pull

A vibe-coding repo for trying to pull data from Garmin connect. Something's clearly incorrect so figured I'd put it here.

- This primarily leverages https://github.com/cyberjunky/python-garminconnect?tab=readme-ov-file
- I used Claude, ChatGPT, Copilot (because I don't pay for any of them) to create python
- It's failing somewhere but after two hours of creating, playing, and debugging it, I couldn't figure it out
- This (https://github.com/tcgoetz/GarminDB?tab=readme-ov-file) also seems interesting but I don't think it's needed

The goal of this repo (python file) is to:
- Leverage the API Wrapper to connect to Garmin Connect
- Extract HRV/RHR/Sleep/Sleep Quality Data over the last year into a CSV
- Add the dates I was sick to the CSV

Then my plan is to upload that to an LLM for analysis. It's already had some interesting - though probably unsurpising - results with my 90 days of data:

> Illness Prevention Insights -
> Your data suggests two distinct illness episodes (January 2-17 and March 7-29).
>
> The days immediately preceding these episodes show:

> - A drop in HRV by 5+ points from your baseline
> - Sleep Score falling below 70 for consecutive nights
> - Resting HR increasing by 1-2 BPM
