package com.querypilot.dataset;

import com.querypilot.common.ApiResponse;
import com.querypilot.dataset.dto.DatasetDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final DatasetService datasetService;

    public DatasetController(DatasetService datasetService) {
        this.datasetService = datasetService;
    }

    @GetMapping
    public ApiResponse<List<DatasetDto>> list() {
        return ApiResponse.ok(datasetService.listDatasets());
    }
}
