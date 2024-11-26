package pl.matelcode;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.ConfigurableApplicationContext;

@SpringBootApplication(scanBasePackages = {"pl.matelcode"})
@EntityScan(basePackages = "pl.matelcode.domains")
@EnableCaching
public class App {

	public static void main(String[] args) throws InterruptedException {
		ConfigurableApplicationContext run = SpringApplication.run(App.class, args);

// starter.start teraz ma EventListener - ApplicationReadyApplication
//		AppStarter starter = run.getBean(AppStarter.class);
//		starter.start();
	}
}


