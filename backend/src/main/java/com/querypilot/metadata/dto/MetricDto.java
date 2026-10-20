package com.querypilot.metadata.dto;

import com.querypilot.metadata.BusinessMetric;

public record MetricDto(Long id, String name, String definition, String expression, String timeColumn,
                        String synonyms) {

    public static MetricDto from(BusinessMetric metric) {
        return new MetricDto(metric.getId(), metric.getName(), metric.getDefinition(),
                metric.getExpression(), metric.getTimeColumn(), metric.getSynonyms());
    }
}
