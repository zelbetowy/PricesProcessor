package pl.matelcode.domains.priceProcessed.model.DTO;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PriceProcessedDTO {
    private Long symbolId; // Symbol jako ID w JSON-ie
    private LocalDateTime timestamp;
    private Long serverTimeRaw;
    private BigDecimal last;
}
