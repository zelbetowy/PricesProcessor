package pl.matelcode.AppStarter;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class HttpCaller {

    @Autowired
    private  RestTemplate restTemplate;


    public void callEndpointProvider(String url, String config) {
        String fullUrl = url + "?config=" + config;
        try {
            String response = restTemplate.getForObject(fullUrl, String.class);
            System.out.println("Response from server: " + response);

        } catch (Exception e) {

            System.err.println("Failed to call endpoint: " + fullUrl);
            e.printStackTrace();
        }
    }

}
