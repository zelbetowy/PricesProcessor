package pl.matelcode.domains.price.model;

import jakarta.persistence.*;
import lombok.*;
import pl.matelcode.domains.symbol.model.Symbol;

import java.math.BigDecimal;
import java.time.LocalDateTime;


@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Entity
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@Table(name = "price_thick")
public class PriceThick  {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(cascade = CascadeType.ALL, fetch=FetchType.EAGER)
    @JoinColumn(name = "symbol_id", nullable = false, unique = true)
//    @EqualsAndHashCode.Include  // To jest po to, zeby metody equals i hashkode uwzględnialy tylko ID symbol.
    private Symbol symbol; // Klucz obcy do symbol_id

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "server_time_raw", nullable = false)
    private Long serverTimeRaw;

    @Column(name = "last", nullable = false)
    private BigDecimal last;
}
