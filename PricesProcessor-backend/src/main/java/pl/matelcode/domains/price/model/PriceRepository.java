package pl.matelcode.domains.price.model;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PriceRepository extends JpaRepository<Price, Long> {

        @Query("SELECT DISTINCT p.symbol.id FROM Price p")
        List<Long> findDistinctSymbolIds();

        // Zwraca najnowsze `n` rekordów
        @Query("SELECT p FROM Price p ORDER BY p.timestamp DESC")
        List<Price> findTopNPrices(Pageable pageable);

        @Query("SELECT p FROM Price p WHERE p.symbol.id = :symbolId ORDER BY p.timestamp DESC")
        List<Price> findLatestPricesBySymbolId(@Param("symbolId") int symbolId, Pageable pageable);
}
