package pl.matelcode.symbol.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.ArrayList;
import java.util.List;

public interface SymbolRepository extends JpaRepository<Symbol, Long> {

    @Query("SELECT tagFpMarkets FROM Symbol")
    ArrayList<String>findAllTagFpMarkets();


    @Query("SELECT tagIcMarkets FROM Symbol")
    ArrayList<String> findAllTagIcMarkets();

}
