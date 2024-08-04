package pl.matelcode.Kutarate;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.ParameterizedPreparedStatementSetter;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/SqlApi")
public class SQLController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping("/executeSQL")
    public String executeSQL(@RequestBody String sql) {
        try {
            jdbcTemplate.execute(sql);
            return "SQL executed successfully.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to execute SQL: " + e.getMessage();
        }
    }

    @GetMapping("/clearDatabase")
    public String clearDatabase() {
        try {
            jdbcTemplate.execute("DROP ALL OBJECTS");
            return "Database cleared successfully.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to clear database: " + e.getMessage();
        }
    }

    @PostMapping("/insertData")
    public String insertData(@RequestBody List<Map<String, Object>> data) {
        if (data.isEmpty()) {
            return "No data to insert.";
        }


        String tableName = "FOREX_PROCESSDATA.PRICESPROCESSED_" + data.get(0).get("symbol");
        String sql = "INSERT INTO " + tableName + " (TIMESTAMP, LAST) VALUES (?, ?)";

        try {
            jdbcTemplate.batchUpdate(sql, data, data.size(),
                    new ParameterizedPreparedStatementSetter<Map<String, Object>>() {
                        public void setValues(PreparedStatement ps, Map<String, Object> argument) throws SQLException {
                            ps.setTimestamp(1, Timestamp.valueOf((String) argument.get("timestamp")));
                            ps.setBigDecimal(2, new BigDecimal(argument.get("last").toString()));
                        }
                    });
            return "Data inserted successfully.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Failed to insert data: " + e.getMessage();
        }
    }


    @PostMapping("/querySQL")
    public List<Map<String, Object>> querySQL(@RequestBody String sql) {
        try {
            return jdbcTemplate.query(sql, (ResultSet rs) -> {
                List<Map<String, Object>> list = new ArrayList<>();
                int columnCount = rs.getMetaData().getColumnCount();
                while (rs.next()) {
                    Map<String, Object> row = new HashMap<>();
                    for (int i = 1; i <= columnCount; i++) {
                        row.put(rs.getMetaData().getColumnName(i), rs.getObject(i));
                    }
                    list.add(row);
                }
                return list;
            });
        } catch (Exception e) {
            e.printStackTrace();
            List<Map<String, Object>> errorResponse = new ArrayList<>();
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            errorResponse.add(error);
            return errorResponse;
        }
    }
}
