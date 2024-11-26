package pl.matelcode.domains.priceProcessed.service;

import org.junit.jupiter.api.Test;
import pl.matelcode.domains.priceProcessed.model.DTO.PriceProcessedDTO;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PriceProcessedServiceTest {

    @Test
    void testMapDtosToSqlValues() {


        //Dane wejsciowe deklarujemy ręcznie:
        PriceProcessedDTO dto1 = new PriceProcessedDTO();
        dto1.setSymbolId(1L);
        dto1.setTimestamp(LocalDateTime.parse("2024-11-25T13:57:40"));
        dto1.setServerTimeRaw(1732543060L);
        dto1.setLast(new BigDecimal("3491.468"));

        PriceProcessedDTO dto2 = new PriceProcessedDTO();
        dto2.setSymbolId(2L);
        dto2.setTimestamp(LocalDateTime.parse("2024-11-25T13:57:40"));
        dto2.setServerTimeRaw(1732543060L);
        dto2.setLast(new BigDecimal("97.728"));

        List<PriceProcessedDTO> batch = Arrays.asList(dto1, dto2);
        PriceProcessedService service = new PriceProcessedService();



        String result = service.mapDtosToSqlValues(batch);
        String expected = "(1, '2024-11-25T13:57:40', 1732543060, 3491.468), " +
                "(2, '2024-11-25T13:57:40', 1732543060, 97.728)";

        // Sprawdzenie wyniku
        assertEquals(expected, result);
    }
}
