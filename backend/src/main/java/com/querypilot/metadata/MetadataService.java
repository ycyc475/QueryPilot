package com.querypilot.metadata;

import com.querypilot.common.BusinessException;
import com.querypilot.dataset.DatasetRepository;
import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.RelationDto;
import com.querypilot.metadata.dto.SchemaDto;
import com.querypilot.metadata.dto.TableDto;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class MetadataService {

    private final DatasetRepository datasetRepository;
    private final SchemaTableRepository tableRepository;
    private final SchemaColumnRepository columnRepository;
    private final SchemaRelationRepository relationRepository;
    private final BusinessMetricRepository metricRepository;

    public MetadataService(DatasetRepository datasetRepository,
                           SchemaTableRepository tableRepository,
                           SchemaColumnRepository columnRepository,
                           SchemaRelationRepository relationRepository,
                           BusinessMetricRepository metricRepository) {
        this.datasetRepository = datasetRepository;
        this.tableRepository = tableRepository;
        this.columnRepository = columnRepository;
        this.relationRepository = relationRepository;
        this.metricRepository = metricRepository;
    }

    /**
     * 返回数据集「获授权」的完整语义元数据（仅 is_accessible=true 的表及其字段）。
     */
    @Transactional(readOnly = true)
    public SchemaDto getSchema(Long datasetId) {
        if (!datasetRepository.existsById(datasetId)) {
            throw new BusinessException(HttpStatus.NOT_FOUND, "数据集不存在: " + datasetId);
        }
        List<SchemaTable> tables = tableRepository.findByDatasetIdAndAccessibleTrueOrderByIdAsc(datasetId);
        Map<Long, List<ColumnDto>> columnsByTable = columnRepository
                .findByTableIdInOrderByIdAsc(tables.stream().map(SchemaTable::getId).toList())
                .stream()
                .collect(Collectors.groupingBy(SchemaColumn::getTableId,
                        Collectors.mapping(ColumnDto::from, Collectors.toList())));
        List<TableDto> tableDtos = tables.stream()
                .map(t -> TableDto.from(t, columnsByTable.getOrDefault(t.getId(), List.of())))
                .toList();
        List<RelationDto> relations = relationRepository.findByDatasetIdOrderByIdAsc(datasetId)
                .stream().map(RelationDto::from).toList();
        List<MetricDto> metrics = metricRepository.findByDatasetIdOrderByIdAsc(datasetId)
                .stream().map(MetricDto::from).toList();
        return new SchemaDto(datasetId, tableDtos, relations, metrics);
    }
}
