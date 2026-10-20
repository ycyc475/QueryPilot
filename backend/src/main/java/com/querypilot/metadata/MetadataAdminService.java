package com.querypilot.metadata;

import com.querypilot.common.BusinessException;
import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.ColumnUpdateRequest;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricUpdateRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 管理员语义维护：编辑指标口径与字段描述/同义词（对应 PRD F10）。
 */
@Service
public class MetadataAdminService {

    private final BusinessMetricRepository metricRepository;
    private final SchemaColumnRepository columnRepository;

    public MetadataAdminService(BusinessMetricRepository metricRepository,
                                SchemaColumnRepository columnRepository) {
        this.metricRepository = metricRepository;
        this.columnRepository = columnRepository;
    }

    @Transactional
    public MetricDto updateMetric(Long id, MetricUpdateRequest request) {
        BusinessMetric metric = metricRepository.findById(id)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "指标不存在: " + id));
        if (request.name() != null) {
            metric.setName(request.name());
        }
        if (request.definition() != null) {
            metric.setDefinition(request.definition());
        }
        if (request.expression() != null) {
            metric.setExpression(request.expression());
        }
        if (request.timeColumn() != null) {
            metric.setTimeColumn(request.timeColumn());
        }
        if (request.synonyms() != null) {
            metric.setSynonyms(request.synonyms());
        }
        return MetricDto.from(metricRepository.save(metric));
    }

    @Transactional
    public ColumnDto updateColumn(Long id, ColumnUpdateRequest request) {
        SchemaColumn column = columnRepository.findById(id)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "字段不存在: " + id));
        if (request.description() != null) {
            column.setDescription(request.description());
        }
        if (request.synonyms() != null) {
            column.setSynonyms(request.synonyms());
        }
        return ColumnDto.from(columnRepository.save(column));
    }
}
