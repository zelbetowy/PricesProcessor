package pl.matelcode.prices.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pl.matelcode.foundation.domain.BaseEntity;
import pl.matelcode.symbol.domain.Symbol;
import pl.matelcode.symbol.domain.SymbolMainMarket;
import pl.matelcode.symbol.domain.SymbolType;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;


@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Entity
public class Prices extends BaseEntity {


    @ManyToOne
    @JoinColumn(name = "symbol_id", nullable = false)
    private String symbol;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "server_time_raw", nullable = false)
    private Long serverTimeRaw;

    @Column(name = "bid", nullable = false)
    private BigDecimal bid;

    @Column(name = "ask", nullable = false)
    private BigDecimal ask;

    @Column(name = "last", nullable = false)
    private BigDecimal last;



}
