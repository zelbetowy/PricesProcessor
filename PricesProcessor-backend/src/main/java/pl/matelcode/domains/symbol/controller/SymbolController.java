package pl.matelcode.domains.symbol.controller;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pl.matelcode.domains.symbol.model.Symbol;
import pl.matelcode.domains.symbol.service.SymbolService;

import java.util.List;

@RestController
@RequestMapping("/symbols")
public class SymbolController {

    private final SymbolService symbolService;
    private List<String> symbols;

    @Autowired
    public SymbolController(SymbolService symbolService) {
        this.symbolService = symbolService;
    }


    @PostMapping("/add")
    public ResponseEntity<Symbol> addSymbol(@RequestBody Symbol symbol) {

        System.out.println("recived symbol: " + symbol);
        Symbol symbol1 = symbolService.saveSymbol(symbol);
        return ResponseEntity.ok(symbol1);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Symbol> getSymbolById(@PathVariable Long id) {
        return symbolService.findSymbolById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }


}
