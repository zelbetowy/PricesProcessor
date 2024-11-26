package pl.matelcode.domains.price.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pl.matelcode.domains.price.controller.model.PriceDTO;
import pl.matelcode.domains.price.model.*;
import pl.matelcode.domains.price.service.PriceService;
import pl.matelcode.domains.priceProcessed.model.PriceProcessedRepository;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/prices")
public class PriceController {

    @Autowired
    private PriceService priceService;

    @Autowired
    private PriceProcessedRepository priceProcessedRepository;

    @Autowired
    private PriceRepository priceRepository;


    @PostMapping("/add")
    public ResponseEntity<String> addPrice(@RequestBody PriceDTO priceDto) {
        try {
            priceService.savePriceFromDto(priceDto);
            return ResponseEntity.ok("Price added successfully");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Failed to add price: " + e.getMessage());
        }
    }

    // Obsługa batchow JSON-ów
    @PostMapping("/batch-add")
    public ResponseEntity<String> addPricesBatch(@RequestBody List<PriceDTO> priceDtos) {
        try {
            priceService.savePricesFromDtos(priceDtos);
            return ResponseEntity.ok("Prices batch added successfully");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Failed to add prices-batch: " + e.getMessage());
        }
    }



    @GetMapping("/activesymbols")
    public ResponseEntity<List<Long>> getActiveSymbolsIds() {
        List<Long> activeSymbolsIds = priceRepository.findDistinctSymbolIds();
        if (activeSymbolsIds.isEmpty()) {
            // Zwracamy 204 No Content, odpowiedz, jesli akurat nic nie pracuje.
            return ResponseEntity.noContent().build();
        } else
        {
            return ResponseEntity.ok(activeSymbolsIds);
            // Zwracamy 200 OK, jeśli lista zawiera dane
        }
    }

    @GetMapping("/latest")
    public ResponseEntity<List<Map<String, Object>>> getPreparedLatestPrices(
            @RequestParam int symbolId,
            @RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> preparedPrices = priceService.getPreparedLatestPrices(symbolId, limit);
        if (preparedPrices.isEmpty()) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.ok(preparedPrices);
    }
}
