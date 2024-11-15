package pl.matelcode.symbol.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import pl.matelcode.foundation.domain.BaseEntity;


// Dziedziczmy po @MappedSuperClass
// Data, - gettery, settery, equals i hashCode

@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
@Entity
@Table(name = "symbol")
public class Symbol extends BaseEntity {


    @Column(name = "symbol_full_name")
    private String symbolFullName;

    @Enumerated(EnumType.STRING)
    @Column(name = "main_market")
    private SymbolMainMarket mainStock;

    @Enumerated(EnumType.STRING)
    @Column(name = "type")
    private SymbolType symbolType;

    @Column (name = "tag_fpmarkets")
    private String tagFpMarkets;

    @Column (name = "tag_icmarkets")
    private String tagIcMarkets;

    @Column (name = "isin", nullable = true)
    private String isin;

    @Column (name = "us100_flag")
    private boolean us100flag;

    @Column (name = "us500_flag")
    private boolean us500flag;


}
