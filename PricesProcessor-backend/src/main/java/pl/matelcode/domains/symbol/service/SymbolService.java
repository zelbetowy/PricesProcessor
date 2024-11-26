package pl.matelcode.domains.symbol.service;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import pl.matelcode.domains.symbol.model.Symbol;
import pl.matelcode.domains.symbol.model.SymbolRepository;
import pl.matelcode.domains.symbol.model.SymbolType;

import java.util.ArrayList;
import java.util.Optional;


@Service
public class SymbolService {


    private final SymbolRepository symbolRepository;

    @Autowired
    public SymbolService(SymbolRepository symbolRepository) {
        this.symbolRepository = symbolRepository;
    }

    public Symbol saveSymbol (Symbol symbol) {
        return symbolRepository.save(symbol);
    }

    @Cacheable(value = "symbolCache", key = "#id")
    public Optional<Symbol> findSymbolById(Long id) {
        return symbolRepository.findById(id);
    }

    public  ArrayList<String> getAllTagFpMarkets() {
        return symbolRepository.findAllTagFpMarkets();
    }


    public ArrayList<String> getAllTagIcMarkets() {
        return symbolRepository.findAllTagFpMarkets();
    }


    public ArrayList<String> getAllTagFpMarketsByType(String type) {
        SymbolType symbolType = SymbolType.valueOf(type);
        System.out.println(symbolType.toString());
        return symbolRepository.findAllTagFpMarketsByType(symbolType);
    }


    public ArrayList<String> getAllTagIcMarketsByType(String type) {
        SymbolType symbolType = SymbolType.valueOf(type);
        System.out.println(symbolType.toString());
        return symbolRepository.findAllTagIcMarketsByType(symbolType);
    }




    public ArrayList<String> getAllTagBinanceByType(String type) {
        SymbolType symbolType = SymbolType.valueOf(type);
        System.out.println(symbolType.toString());
        return symbolRepository.findAllTagBinanceByType(symbolType);
    }





    @Cacheable(value = "symbolCache", key = "#tag + ':' + #server")
    public Symbol getSymbolByTagAndServer(String tag, String server) {
        if (server.toLowerCase().contains("fp")) {
            return symbolRepository.findByTagFpMarkets(tag)
                    .orElseThrow(() -> new RuntimeException("Symbol not found for FPmarkets tag: " + tag));
        } else if (server.toLowerCase().contains("ic")) {
            return symbolRepository.findByTagIcMarkets(tag)
                    .orElseThrow(() -> new RuntimeException("Symbol not found for ICMarkets tag: " + tag));
        } else {
            throw new IllegalArgumentException("Unknown server: " + server);
        }
    }

}

