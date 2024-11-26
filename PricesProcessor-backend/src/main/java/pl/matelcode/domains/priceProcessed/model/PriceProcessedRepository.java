package pl.matelcode.domains.priceProcessed.model;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.web.bind.annotation.RequestParam;

import java.math.BigDecimal;


@Repository
public interface PriceProcessedRepository extends JpaRepository<PriceProcessed, Long> {

    @Modifying
    @Query(value = "INSERT INTO price_processed (symbol_id, timestamp, server_time_raw, \"last\") " +
            "VALUES (:batch " +
            " ON CONFLICT (symbol_id, timestamp) DO NOTHING ; ", nativeQuery = true)
    void batchInsert(@Param("batch") String batch);


}
