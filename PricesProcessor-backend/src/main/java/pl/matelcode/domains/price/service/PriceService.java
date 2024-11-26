package pl.matelcode.domains.price.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pl.matelcode.domains.price.controller.model.PriceDTO;
import pl.matelcode.domains.price.model.Price;
import pl.matelcode.domains.price.model.PriceRepository;
import pl.matelcode.domains.price.model.PriceThick;
import pl.matelcode.domains.price.model.PriceThickRepository;
import pl.matelcode.domains.symbol.service.SymbolService;
import pl.matelcode.domains.symbol.model.Symbol;

import java.util.List;
import java.util.Map;

@Service
public class PriceService {

    @Autowired
    private PriceRepository priceRepository;
    @Autowired
    private PriceThickRepository priceThickRepository;
    @Autowired
    private SymbolService symbolService;


    @Transactional
    public void savePriceFromDto (PriceDTO priceRequestDTO) {
        Symbol symbol = symbolService.getSymbolByTagAndServer(priceRequestDTO.getTag(), priceRequestDTO.getServer());

        Price price = new Price();
        price.setSymbol(symbol);
        price.setTimestamp(priceRequestDTO.getTimestamp());
        price.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
        price.setBid(priceRequestDTO.getBid());
        price.setAsk(priceRequestDTO.getAsk());
        price.setLast(priceRequestDTO.getLast());
        priceRepository.save(price);

        PriceThick existingPriceThick = priceThickRepository.findBySymbol(symbol);
        if (existingPriceThick != null) {
            existingPriceThick.setTimestamp(priceRequestDTO.getTimestamp());
            existingPriceThick.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
            existingPriceThick.setLast(priceRequestDTO.getLast());
            priceThickRepository.save(existingPriceThick);
        } else {
            PriceThick savedPriceThick = new PriceThick();
            savedPriceThick.setSymbol(symbol);
            savedPriceThick.setTimestamp(priceRequestDTO.getTimestamp());
            savedPriceThick.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
            savedPriceThick.setLast(priceRequestDTO.getLast());
            priceThickRepository.save(savedPriceThick);
        }
    }

    @Transactional
    public void savePricesFromDtos(List<PriceDTO> priceRequestsDTO) {
        priceRequestsDTO.forEach(priceRequestDTO -> {
            // Pobranie Symbol dla bieżącego DTO
            Symbol symbol = symbolService.getSymbolByTagAndServer(priceRequestDTO.getTag(), priceRequestDTO.getServer());

            // Tworzenie i zapis encji Price
            Price price = new Price();
            price.setSymbol(symbol);
            price.setTimestamp(priceRequestDTO.getTimestamp());
            price.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
            price.setBid(priceRequestDTO.getBid());
            price.setAsk(priceRequestDTO.getAsk());
            price.setLast(priceRequestDTO.getLast());
            priceRepository.save(price);

            // Sprawdzenie, czy istnieje już rekord PriceThick dla Symbol
            PriceThick existingPriceThick = priceThickRepository.findBySymbol(symbol);
            if (existingPriceThick == null) {

                // Tworzenie nowego rekordu PriceThick
                PriceThick newPriceThick = new PriceThick();
                newPriceThick.setSymbol(symbol);
                newPriceThick.setTimestamp(priceRequestDTO.getTimestamp());
                newPriceThick.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
                newPriceThick.setLast(priceRequestDTO.getLast());
                priceThickRepository.save(newPriceThick);

            }else {
            }
                // Aktualizacja istniejącego rekordu PriceThick
                existingPriceThick.setTimestamp(priceRequestDTO.getTimestamp());
                existingPriceThick.setServerTimeRaw(priceRequestDTO.getServerTimeRaw());
                existingPriceThick.setLast(priceRequestDTO.getLast());
                priceThickRepository.save(existingPriceThick);

        });
    }

    public List<Price> getActiveSymbols(int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return priceRepository.findTopNPrices(pageable);
    }

    public List<Price> getLatestPrices(int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return priceRepository.findTopNPrices(pageable);
    }

    public List<Map<String, Object>> getPreparedLatestPrices(int symbolId, int limit) {
        Pageable pageable = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "timestamp"));
        List<Price> prices = priceRepository.findLatestPricesBySymbolId(symbolId, pageable);

        return prices.stream().map(this::convertToMap).toList();
    }

    private Map<String, Object> convertToMap(Price price) {
        return Map.of(
                "server_time_raw",price.getServerTimeRaw(),
                "last", price.getLast()
        );
    }

}

