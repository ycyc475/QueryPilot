package com.querypilot.metadata;

import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricMatchDto;
import com.querypilot.metadata.dto.RelationDto;
import com.querypilot.metadata.dto.SchemaDto;
import com.querypilot.metadata.dto.SearchResultDto;
import com.querypilot.metadata.dto.TableDto;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(MetadataController.class)
@AutoConfigureMockMvc(addFilters = false)
class MetadataControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private MetadataService metadataService;

    @MockitoBean
    private SemanticSearchService semanticSearchService;

    @Test
    void returnsSchema() throws Exception {
        ColumnDto column = new ColumnDto(1L, "paid_amount", "numeric", "实付金额", "实付金额,销售额", false);
        TableDto table = new TableDto(1L, "orders", "订单主表", "订单", List.of(column));
        RelationDto relation = new RelationDto("orders", "customer_id", "customers", "id", "many_to_one");
        MetricDto metric = new MetricDto(1L, "实付销售额", "已支付订单实付金额之和", "SUM(orders.paid_amount)",
                "ordered_at", "销售额,营收");
        SchemaDto schema = new SchemaDto(1L, List.of(table), List.of(relation), List.of(metric));

        when(metadataService.getSchema(1L)).thenReturn(schema);

        mockMvc.perform(get("/api/datasets/1/schema"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.tables[0].name").value("orders"))
                .andExpect(jsonPath("$.data.tables[0].columns[0].name").value("paid_amount"))
                .andExpect(jsonPath("$.data.metrics[0].name").value("实付销售额"));
    }

    @Test
    void returnsSearchResult() throws Exception {
        MetricDto metric = new MetricDto(1L, "实付销售额", "已支付订单实付金额之和", "SUM(orders.paid_amount)",
                "ordered_at", "销售额,营收");
        SearchResultDto result = new SearchResultDto(1L, "实付销售额",
                List.of(new MetricMatchDto(metric, "实付销售额")), List.of());

        when(semanticSearchService.search(1L, "实付销售额")).thenReturn(result);

        mockMvc.perform(get("/api/datasets/1/semantic-search").param("q", "实付销售额"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.metrics[0].metric.name").value("实付销售额"))
                .andExpect(jsonPath("$.data.metrics[0].matchedTerm").value("实付销售额"));
    }
}
