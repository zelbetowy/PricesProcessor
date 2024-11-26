package pl.matelcode.domains.price.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pl.matelcode.domains.symbol.model.Symbol;

import java.math.BigDecimal;
import java.time.LocalDateTime;


@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Entity
@Table(name = "price_raw")
public class Price  {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "symbol_id", nullable = false)
    private Symbol symbol;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "server_time_raw", nullable = false)
    private Long serverTimeRaw;

    @Column(name = "last", nullable = false)
    private BigDecimal last;

    @Column(name = "ask", nullable = false)
    private BigDecimal ask;

    @Column(name = "bid", nullable = false, precision = 20, scale = 3)
    private BigDecimal bid;
}
