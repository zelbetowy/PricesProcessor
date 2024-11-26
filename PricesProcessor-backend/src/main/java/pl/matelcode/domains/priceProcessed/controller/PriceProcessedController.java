package pl.matelcode.domains.priceProcessed.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pl.matelcode.domains.priceProcessed.model.DTO.PriceProcessedDTO;
import pl.matelcode.domains.priceProcessed.service.PriceProcessedService;
import pl.matelcode.domains.priceProcessed.model.PriceProcessed;
import pl.matelcode.domains.priceProcessed.model.PriceProcessedRepository;

import java.util.List;

@RestController
@RequestMapping("/api/pricesProcesssed")
public class PriceProcessedController {

    @Autowired
    private PriceProcessedRepository priceProcessedRepository;

    @Autowired
    private PriceProcessedService priceProcessedService;



    @PostMapping("/add")
    public ResponseEntity<Void> savePriceProcessed(@RequestBody PriceProcessed priceProcessed) {
        if (priceProcessed == null) {
            return ResponseEntity.badRequest().build();
        }

        try {
            priceProcessedRepository.save(priceProcessed);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            // Logowanie błędu dla diagnostyki
            System.err.println("Error while saving processed price: " + e.getMessage());
            return ResponseEntity.status(500).build();
        }
    }


    @PostMapping("/batch-add")
    public ResponseEntity<?> addPricesBatch(@RequestBody List<PriceProcessedDTO> batch) {
        try {
            priceProcessedService.savePricesProcessedfromDtos(batch);
            return ResponseEntity.ok("Batch processed successfully");
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("An error occurred");
        }
    }
}
