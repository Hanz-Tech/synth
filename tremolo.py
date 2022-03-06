
class Tremolo:
    def __init__(self, depth: float, lfoFreq_Hz: float, sampleRate_Hz: float ) -> None:
        self.depth = depth
        self.lfoDir = 1
        self.lfoCount = 0
        self.lfoCountLimit = 0
        self.sampleRate_Hz = sampleRate_Hz
        self.lfoFreqHz = 0
        self.TremoloSetLFOFrequency(lfoFreq_Hz)
        self.out = 0.0

    def TremoloSetDepth(self, depth: float) -> None:
        if depth < 0.0:
            self.depth = 0.0
        elif depth > 1.0:
            self.depth = 1.0
        else:
            self.depth = depth
        pass

    def TremoloSetLFOFrequency(self, lfoFreq_Hz: float) -> None:
        if lfoFreq_Hz <= 0.0:
            lfoFreq_Hz = 1.0
        #Limit lfo freq to below Nyquitst Frequency
        elif (lfoFreq_Hz > 0.5 * self.sampleRate_Hz):
            lfoFreq_Hz = 0.5 * self.sampleRate_Hz
        
        #Computer counter limit based on desired LFO frequency (countLimit = (fS/fLFO/4) )
        #eg. if sample rate is 44khz and lfo 20hz then count limit = (0.25 * 1/20 ) * 44000
        self.lfoCountLimit = 0.25 * self.sampleRate_Hz / lfoFreq_Hz

        #lfo count within new counter limit range
        if self.lfoCount > self.lfoCountLimit:
            self.lfoCount = self.lfoCountLimit
        elif self.lfoCount < -self.lfoCountLimit:
            self.lfoCount = self.lfoCountLimit

    def TremoloUpdate(self, input: float) -> float:
        
        # y[n] = x[n] * ((1-d) + d * g[n])
        out = input * ( (1.0 - self.depth) + self.depth * self.lfoCount / self.lfoCountLimit )

        if self.lfoCount >= self.lfoCountLimit:
            self.lfoDir = -1
        elif self.lfoCount <= -self.lfoCountLimit:
            self.lfoDir = 1
        
        self.lfoCount += self.lfoDir
        return out 

    def TremoloGet(self, input: float) -> float:
        return input * ( (1.0 - self.depth) + self.depth * self.lfoCount / self.lfoCountLimit )