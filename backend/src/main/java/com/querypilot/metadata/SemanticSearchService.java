package com.querypilot.metadata;

import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.ColumnMatchDto;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricMatchDto;
import com.querypilot.metadata.dto.SchemaDto;
import com.querypilot.metadata.dto.SearchResultDto;
import com.querypilot.metadata.dto.TableDto;
import com.querypilot.metadata.dto.TableMatchDto;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * 词典/关键词召回：将查询文本与授权元数据（表/字段/指标的名称、同义词）做子串匹配，
 * 返回命中结果与召回依据（matchedTerm）。第一版不做向量检索（PRD §6 允许先词典化）。
 */
@Service
public class SemanticSearchService {

    private final MetadataService metadataService;

    public SemanticSearchService(MetadataService metadataService) {
        this.metadataService = metadataService;
    }

    public SearchResultDto search(Long datasetId, String query) {
        SchemaDto schema = metadataService.getSchema(datasetId);
        String q = query == null ? "" : query.trim();

        List<MetricMatchDto> metricMatches = new ArrayList<>();
        for (MetricDto metric : schema.metrics()) {
            String term = matchAny(q, metric.name(), metric.synonyms());
            if (term != null) {
                metricMatches.add(new MetricMatchDto(metric, term));
            }
        }

        List<TableMatchDto> tableMatches = new ArrayList<>();
        for (TableDto table : schema.tables()) {
            String tableTerm = matchAny(q, table.name(), table.synonyms());
            List<ColumnMatchDto> columnMatches = new ArrayList<>();
            for (ColumnDto column : table.columns()) {
                String columnTerm = matchAny(q, column.name(), column.synonyms());
                if (columnTerm != null) {
                    columnMatches.add(new ColumnMatchDto(column, columnTerm));
                }
            }
            if (tableTerm != null || !columnMatches.isEmpty()) {
                tableMatches.add(new TableMatchDto(table, tableTerm, columnMatches));
            }
        }

        return new SearchResultDto(datasetId, q, metricMatches, tableMatches);
    }

    /**
     * 返回 name/synonyms 中最长的命中词；无命中返回 null。
     */
    private String matchAny(String query, String name, String synonyms) {
        if (query.isEmpty()) {
            return null;
        }
        String best = null;
        List<String> terms = new ArrayList<>();
        if (name != null && !name.isBlank()) {
            terms.add(name);
        }
        if (synonyms != null) {
            for (String s : synonyms.split("[,，]")) {
                if (!s.isBlank()) {
                    terms.add(s.trim());
                }
            }
        }
        for (String term : terms) {
            if (query.contains(term) && (best == null || term.length() > best.length())) {
                best = term;
            }
        }
        return best;
    }
}
