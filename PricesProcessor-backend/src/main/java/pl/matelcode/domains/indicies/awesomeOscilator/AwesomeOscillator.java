package pl.matelcode.domains.indicies.awesomeOscilator;

import pl.matelcode.domains.indicies.Indicator;
import pl.matelcode.domains.priceProcessed.model.PriceProcessed;

import java.util.List;

public class AwesomeOscillator implements Indicator {


    @Override
    public String getName() {
        return "Awesome Oscillator";
    }


    @Override
    public double calculate(List<PriceProcessed> prices, long startTimestamp) {
        // Przykładowa logika obliczeń
        double shortMA = calculateMovingAverage(prices, startTimestamp, 5);
        double longMA = calculateMovingAverage(prices, startTimestamp, 34);
        return shortMA - longMA;
    }

    private double calculateMovingAverage(List<PriceProcessed> prices, long startTimestamp, int period) {
        return 0;
//
//
//        prices.stream()
//                .filter((PriceProcessed) p -> p.getTimestamp() >= startTimestamp)
//                .limit(period)
//                .mapToDouble(PriceProcessed::getLast)
//                .average()
//                .orElse(0.0);
    }
}