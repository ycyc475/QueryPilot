package com.querypilot.admin;

import com.querypilot.metadata.MetadataAdminService;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricUpdateRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AdminMetadataController.class)
@AutoConfigureMockMvc(addFilters = false)
class AdminMetadataControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private MetadataAdminService adminService;

    @Test
    void updatesMetric() throws Exception {
        MetricDto updated = new MetricDto(1L, "实付销售额", "新定义", "SUM(orders.paid_amount)",
                "ordered_at", "销售额,营收");
        when(adminService.updateMetric(eq(1L), any(MetricUpdateRequest.class))).thenReturn(updated);

        mockMvc.perform(put("/api/admin/metrics/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"definition\":\"新定义\",\"synonyms\":\"销售额,营收\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.definition").value("新定义"))
                .andExpect(jsonPath("$.data.synonyms").value("销售额,营收"));
    }
}
