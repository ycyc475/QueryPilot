package com.querypilot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class QueryPilotApplication {

	public static void main(String[] args) {
		SpringApplication.run(QueryPilotApplication.class, args);
	}

}
