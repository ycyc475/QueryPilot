package com.querypilot.metadata;

import com.querypilot.common.BusinessException;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricUpdateRequest;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class MetadataAdminServiceTest {

    private final BusinessMetricRepository metricRepository = mock(BusinessMetricRepository.class);
    private final SchemaColumnRepository columnRepository = mock(SchemaColumnRepository.class);
    private final MetadataAdminService service = new MetadataAdminService(metricRepository, columnRepository);

    @Test
    void updatesMetricDefinitionAndSynonyms() {
        BusinessMetric metric = new BusinessMetric();
        metric.setId(1L);
        metric.setName("实付销售额");
        metric.setDefinition("旧定义");
        metric.setExpression("SUM(orders.paid_amount)");
        metric.setTimeColumn("ordered_at");
        metric.setSynonyms("销售额");
        when(metricRepository.findById(1L)).thenReturn(Optional.of(metric));
        when(metricRepository.save(any(BusinessMetric.class))).thenAnswer(inv -> inv.getArgument(0));

        MetricDto result = service.updateMetric(1L,
                new MetricUpdateRequest(null, "新定义", null, null, "销售额,营收"));

        assertThat(result.definition()).isEqualTo("新定义");
        assertThat(result.synonyms()).isEqualTo("销售额,营收");
        assertThat(result.name()).isEqualTo("实付销售额");
        verify(metricRepository).save(metric);
    }

    @Test
    void throwsWhenMetricNotFound() {
        when(metricRepository.findById(999L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.updateMetric(999L, new MetricUpdateRequest(null, null, null, null, null)))
                .isInstanceOf(BusinessException.class);
    }
}
