package pl.matelcode.domains.indicies;

import pl.matelcode.domains.priceProcessed.model.PriceProcessed;

import java.util.List;

public interface Indicator {

    String getName(); // Nazwa wskaźnika
    double calculate(List<PriceProcessed> prices, long startTimestamp); // Obliczanie wskaźnika
}

