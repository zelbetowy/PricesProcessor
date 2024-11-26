package pl.matelcode.domains.priceProcessed.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pl.matelcode.domains.symbol.model.Symbol;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Table(name = "price_processed", uniqueConstraints = @UniqueConstraint(columnNames = {"symbol_id", "timestamp"}))
public class PriceProcessed {

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

    @Column(name = "last", nullable = false, precision = 20, scale = 3)
    private BigDecimal last;

}
