package pl.matelcode.Kutarate;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class KutarateApplication {

	public static void main(String[] args) {
		SpringApplication.run(KutarateApplication.class, args);
	}

	System.out.println("=====================================");
		System.out.println("Welcome to Prices Monitor!");
		System.out.println("Running on Java version: " + System.getProperty("java.version"));
		System.out.println("Java vendor: " + System.getProperty("java.vendor"));
		System.out.println("Java home: " + System.getProperty("java.home"));
		System.out.println("Java vendor URL: " + System.getProperty("java.vendor.url"));
		System.out.println("OS name: " + System.getProperty("os.name"));
		System.out.println("=====================================");

	ConfigurableApplicationContext run = SpringApplication.run(App.class, args);
	AppStarter appStarter = run.getBean(AppStarter.class);
		appStarter.start();
}
