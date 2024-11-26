package pl.matelcode.domains.priceProcessed.model;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import pl.matelcode.domains.priceProcessed.model.PriceProcessed;
import pl.matelcode.domains.priceProcessed.model.PriceProcessedRepository;
import static org.junit.jupiter.api.Assertions.assertEquals;

@DataJpaTest
class PriceProcessedRepositoryTest {
    @Autowired
    private PriceProcessedRepository priceProcessedRepository;

    @Test
    void testBatchInsert() {


        String values = "(1, '2024-11-25T13:57:40', 1732543060, 3491.468), " +
                "(2, '2024-11-25T13:57:40', 1732543060, 97.728)";

        // Wywołanie metody batchInsert z przygotowanymi danymi
        priceProcessedRepository.batchInsert(values);

        // Pobieramy zapisane dane z bazy
        // Sprawdzamy, czy dane zostały zapisane poprawnie
        PriceProcessed priceProcessed1 = priceProcessedRepository.findById(1L).orElse(null);
        PriceProcessed priceProcessed2 = priceProcessedRepository.findById(2L).orElse(null);

        // Sprawdzenie wyników
        assertEquals(1L, priceProcessed1.getSymbol());
        assertEquals("2024-11-25T13:57:40", priceProcessed1.getTimestamp());
        assertEquals(1732543060L, priceProcessed1.getServerTimeRaw());
        assertEquals(3491.468, priceProcessed1.getLast());

        assertEquals(2L, priceProcessed2.getSymbol());
        assertEquals("2024-11-25T13:57:40", priceProcessed2.getTimestamp());
        assertEquals(1732543060L, priceProcessed2.getServerTimeRaw());
        assertEquals(97.728, priceProcessed2.getLast());
    }
}
