package pl.matelcode.JavaServicesRunner;

import com.binance.connector.client.impl.SpotClientImpl;

import java.util.HashMap;
import java.util.Map;

public class BinanceAPI {
    private final SpotClientImpl client;

    // Konstruktor bez kluczy API (dla publicznych endpointów)
    public BinanceAPI() {
        this.client = new SpotClientImpl();
    }

    // Konstruktor z kluczami API (dla prywatnych endpointów, jeśli potrzebne)
    public BinanceAPI(String apiKey, String secretKey) {
        this.client = new SpotClientImpl(apiKey, secretKey);
    }

    /**
     * Pobiera aktualną cenę dla podanego symbolu.
     *
     * @param symbol Symbol pary walutowej, np. BTCUSDT
     * @return Aktualna cena jako double
     * @throws Exception Jeśli wystąpi błąd w komunikacji z Binance API
     */
//    public double getPrice(String symbol) throws Exception {
//        Map<String, Object> parameters = new HashMap<>();
//        parameters.put("symbol", symbol);
//
//        try {
//            // Wywołanie endpointu ticker/price
//            String response = client.createMarket().tickerPrice(parameters);
//
//            // Parsowanie odpowiedzi JSON
//            String priceString = parseJsonValue(response, "price");
//            return Double.parseDouble(priceString);
//        } catch (Exception e) {
//            throw new Exception("Błąd podczas pobierania ceny dla symbolu " + symbol + ": " + e.getMessage());
//        }
//    }

    /**
     * Pomocnicza metoda do parsowania wartości JSON
     *
     * @param json   Odpowiedź JSON
     * @param key    Klucz, którego wartość chcemy wyciągnąć
     * @return Wartość jako String
     */
    private String parseJsonValue(String json, String key) {
        int keyIndex = json.indexOf("\"" + key + "\":");
        if (keyIndex == -1) {
            throw new RuntimeException("Nie znaleziono klucza " + key + " w odpowiedzi JSON.");
        }

        int valueStart = json.indexOf("\"", keyIndex + key.length() + 3) + 1;
        int valueEnd = json.indexOf("\"", valueStart);
        return json.substring(valueStart, valueEnd);
    }

//    public static void main(String[] args) {
//        try {
//            BinanceAPI binanceAPI = new BinanceAPI();
//            String symbol = "BTCUSDT";
//            double price = binanceAPI.getPrice(symbol);
//            System.out.println("Aktualna cena " + symbol + ": " + price);
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//    }
}
