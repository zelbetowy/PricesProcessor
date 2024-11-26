package pl.matelcode.domains.symbol.model;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.Optional;

@Repository
public interface SymbolRepository extends JpaRepository<Symbol, Long> {

    @Query("SELECT tagFpMarkets FROM Symbol")
    ArrayList<String>findAllTagFpMarkets();


    @Query("SELECT tagIcMarkets FROM Symbol")
    ArrayList<String> findAllTagIcMarkets();

    @Query("SELECT tagFpMarkets FROM Symbol s WHERE s.symbolType = :symbolType")
    ArrayList<String> findAllTagFpMarketsByType(@Param("symbolType") SymbolType symbolType);

    @Query("SELECT tagFpMarkets FROM Symbol s WHERE s.symbolType = :symbolType")
    ArrayList<String> findAllTagIcMarketsByType(@Param("symbolType") SymbolType symbolType);


    @Query("SELECT tagBinance FROM Symbol s WHERE s.symbolType = :symbolType")
    ArrayList<String> findAllTagBinanceByType(@Param("symbolType") SymbolType symbolType);


    // Dla providera FPMarkets
    Optional<Symbol> findByTagFpMarkets(String tagFpMarkets);

    // Dla providera ICMarkets
    Optional<Symbol> findByTagIcMarkets(String tagIcMarkets);





}
