package pl.matelcode.symbol.application;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import pl.matelcode.symbol.domain.Symbol;
import pl.matelcode.symbol.domain.SymbolRepository;

import java.util.ArrayList;
import java.util.List;
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

    public Optional<Symbol> findSymbolById(Long id) {
        return symbolRepository.findById(id);
    }

    public  ArrayList<String> getAllTagFpMarkets() {
        return symbolRepository.findAllTagFpMarkets();
    }


    public ArrayList<String> getAllTagIcMarkets() {
        return symbolRepository.findAllTagFpMarkets();
    }
}
