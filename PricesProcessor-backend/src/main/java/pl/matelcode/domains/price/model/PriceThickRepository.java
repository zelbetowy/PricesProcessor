package pl.matelcode.domains.price.model;

import org.springframework.data.jpa.repository.JpaRepository;
import pl.matelcode.domains.symbol.model.Symbol;

public interface PriceThickRepository extends JpaRepository<PriceThick, Long> {


    PriceThick findBySymbol(Symbol symbol);

}
