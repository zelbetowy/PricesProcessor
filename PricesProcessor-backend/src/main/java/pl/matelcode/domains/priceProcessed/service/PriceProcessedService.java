package pl.matelcode.domains.priceProcessed.service;

import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import pl.matelcode.domains.priceProcessed.model.DTO.PriceProcessedDTO;
import pl.matelcode.domains.priceProcessed.model.PriceProcessed;
import pl.matelcode.domains.priceProcessed.model.PriceProcessedRepository;
import pl.matelcode.domains.symbol.service.SymbolService;
import pl.matelcode.domains.symbol.model.Symbol;

import java.util.List;
import java.util.Optional;
import java.util.StringJoiner;

@Service
public class PriceProcessedService {

    @Autowired
    private PriceProcessedRepository priceProcessedRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;


    @Transactional
    public void savePricesProcessedfromDtos(List<PriceProcessedDTO> batch) {
        if (batch == null || batch.isEmpty()) {
            return;
        }
        String processsedBatch = mapDtosToSqlValues(batch);
        StringBuilder stringBuilder = new StringBuilder();
        stringBuilder.append("INSERT INTO price_processed (symbol_id, timestamp, server_time_raw, \"last\") VALUES ");
        stringBuilder.append(processsedBatch);
        stringBuilder.append(" ON CONFLICT (symbol_id, timestamp) DO NOTHING;");
        String input = stringBuilder.toString();

        jdbcTemplate.execute(input);

//        priceProcessedRepository.batchInsert(processsedBatch);
    }

    String mapDtosToSqlValues(List<PriceProcessedDTO> batch) {
        StringBuilder values = new StringBuilder();

        for (int i = 0; i < batch.size(); i++) {
            PriceProcessedDTO dto = batch.get(i);
            values.append("(")
                    .append(dto.getSymbolId()).append(", ")
                    .append("'").append(dto.getTimestamp()).append("', ")
                    .append(dto.getServerTimeRaw()).append(", ")
                    .append(dto.getLast())
                    .append(")");

            // Dodaj przecinek między wierszami, ale nie po ostatnim
            if (i < batch.size() - 1) {
                values.append(", ");
            }
        }

        return values.toString();
    }
}