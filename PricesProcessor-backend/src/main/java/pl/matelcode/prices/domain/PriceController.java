package pl.matelcode.prices.domain;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/prices")
public class PriceController {

    @Autowired
    private PriceRepository priceRepository;

    @PostMapping("/add")
    public Price addPrice(@RequestBody Price price) {
        return priceRepository.save(price);
    }

    @PostMapping("/batch-add")
    public List<Price> addPricesBatch(@RequestBody List<Price> prices) {
        return priceRepository.saveAll(prices);
    }
}