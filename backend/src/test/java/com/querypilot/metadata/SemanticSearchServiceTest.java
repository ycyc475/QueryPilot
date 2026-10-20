package com.querypilot.metadata;

import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.SchemaDto;
import com.querypilot.metadata.dto.SearchResultDto;
import com.querypilot.metadata.dto.TableDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class SemanticSearchServiceTest {

    private SemanticSearchService service;

    @BeforeEach
    void setUp() {
        MetadataService metadataService = mock(MetadataService.class);

        ColumnDto paidAmount = new ColumnDto(7L, "paid_amount", "numeric", "实付金额",
                "实付金额,实付,支付金额,销售额,营收,收入", false);
        ColumnDto province = new ColumnDto(19L, "province", "varchar", "省份", "省份,省", false);
        TableDto orders = new TableDto(1L, "orders", "订单主表", "订单", List.of(paidAmount));
        TableDto customers = new TableDto(3L, "customers", "客户", "客户,用户", List.of(province));
        MetricDto sales = new MetricDto(1L, "实付销售额", "已支付订单实付金额之和", "SUM(orders.paid_amount)",
                "ordered_at", "销售额,营收,收入,GMV");
        SchemaDto schema = new SchemaDto(1L, List.of(orders, customers), List.of(), List.of(sales));

        when(metadataService.getSchema(1L)).thenReturn(schema);
        service = new SemanticSearchService(metadataService);
    }

    @Test
    void matchesMetricAndColumnForSalesQuery() {
        SearchResultDto result = service.search(1L, "实付销售额");

        assertThat(result.metrics()).hasSize(1);
        assertThat(result.metrics().get(0).metric().name()).isEqualTo("实付销售额");
        assertThat(result.tables().stream()
                .filter(t -> t.table().name().equals("orders"))
                .flatMap(t -> t.columns().stream())
                .anyMatch(c -> c.column().name().equals("paid_amount"))).isTrue();
    }

    @Test
    void matchesProvinceColumn() {
        SearchResultDto result = service.search(1L, "按省份拆分");

        assertThat(result.tables().stream()
                .flatMap(t -> t.columns().stream())
                .anyMatch(c -> c.column().name().equals("province"))).isTrue();
    }

    @Test
    void noMatchReturnsEmpty() {
        SearchResultDto result = service.search(1L, "zzzz");

        assertThat(result.metrics()).isEmpty();
        assertThat(result.tables()).isEmpty();
    }
}
