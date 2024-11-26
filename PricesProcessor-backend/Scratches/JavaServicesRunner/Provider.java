package pl.matelcode.JavaServicesRunner;

import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

public class Provider {
    private final String symbol; // Symbol, np. BTCUSDT
    private final long intervalMillis; // Interwał w milisekundach
    private final List<PriceRecord> priceHistory = new ArrayList<>();
    private final BinanceAPI binanceAPI = new BinanceAPI();
    private Timer timer;

    public Provider(String symbol, long intervalMillis) {
        this.symbol = symbol;
        this.intervalMillis = intervalMillis;
    }

    public void startProviding() {
        timer = new Timer();
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                try {
                    double price = binanceAPI.getPrice(symbol);
                    long timestamp = System.currentTimeMillis();
                    priceHistory.add(new PriceRecord(price, timestamp));
                    System.out.println("[" + symbol + "] Zapisano: " + price + " w czasie: " + timestamp);
                } catch (Exception e) {
                    System.err.println("[" + symbol + "] Błąd podczas pobierania ceny: " + e.getMessage());
                    timer.cancel();
                }
            }
        }, 0, intervalMillis);
    }

    public void stopProviding() {
        if (timer != null) {
            timer.cancel();
            System.out.println("[" + symbol + "] Zatrzymano dostarczanie danych.");
        }
    }

    public List<PriceRecord> getPriceHistory() {
        return new ArrayList<>(priceHistory); // Kopia listy, aby zabezpieczyć dane
    }

    private static class PriceRecord {
        private final double price;
        private final long timestamp;

        public PriceRecord(double price, long timestamp) {
            this.price = price;
            this.timestamp = timestamp;
        }

        public double getPrice() {
            return price;
        }

        public long getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            return "PriceRecord{" +
                    "price=" + price +
                    ", timestamp=" + timestamp +
                    '}';
        }
    }

    private static class BinanceAPI {
        public double getPrice(String symbol) throws Exception {
            // Tu należy użyć rzeczywistego Binance API
            return Math.random() * 1000; // Symulacja losowej ceny
        }
    }
}
