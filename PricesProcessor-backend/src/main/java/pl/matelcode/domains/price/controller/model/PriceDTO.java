package pl.matelcode.domains.price.controller.model;

import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
public class PriceDTO {

    private String tag;
    private LocalDateTime timestamp;
    private long serverTimeRaw;
    private BigDecimal bid;
    private BigDecimal ask;
    private BigDecimal last;
    private String server;

    public PriceDTO(String tag, LocalDateTime timestamp, long serverTimeRaw, BigDecimal bid, BigDecimal ask, BigDecimal last, String server) {
        this.tag = tag;
        this.timestamp = timestamp;
        this.serverTimeRaw = serverTimeRaw;
        this.bid = bid;
        this.ask = ask;
        this.last = last;
        this.server = server;
    }
}