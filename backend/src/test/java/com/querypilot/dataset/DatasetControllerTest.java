package com.querypilot.dataset;

import com.querypilot.dataset.dto.DatasetDto;
import com.querypilot.dataset.dto.DatasetSourceDto;
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

@WebMvcTest(DatasetController.class)
@AutoConfigureMockMvc(addFilters = false)
class DatasetControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DatasetService datasetService;

    @Test
    void listsDatasets() throws Exception {
        DatasetSourceDto source = new DatasetSourceDto(1L, "演示电商分析库", "postgresql");
        when(datasetService.listDatasets())
                .thenReturn(List.of(new DatasetDto(1L, "电商分析", "模拟电商数据", source)));

        mockMvc.perform(get("/api/datasets"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data[0].name").value("电商分析"))
                .andExpect(jsonPath("$.data[0].source.name").value("演示电商分析库"));
    }
}
