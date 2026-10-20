package com.querypilot.dataset;

import com.querypilot.dataset.dto.DatasetDto;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class DatasetService {

    private final DatasetRepository datasetRepository;

    public DatasetService(DatasetRepository datasetRepository) {
        this.datasetRepository = datasetRepository;
    }

    @Transactional(readOnly = true)
    public List<DatasetDto> listDatasets() {
        return datasetRepository.findAllWithSource().stream()
                .map(DatasetDto::from)
                .toList();
    }
}
