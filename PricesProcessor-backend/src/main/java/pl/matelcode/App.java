package pl.matelcode;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import pl.matelcode.AppStarter.AppStarter;

@SpringBootApplication(scanBasePackages = {"pl.matelcode"})
public class App {

	public static void main(String[] args) throws InterruptedException {
		ConfigurableApplicationContext run = SpringApplication.run(App.class, args);

// starter.start teraz ma EventListener - ApplicationReadyApplication
//		AppStarter starter = run.getBean(AppStarter.class);
//		starter.start();
	}

}


