package school.sptech.menor_tempo_atendimento.service;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.mapper.NoGrafoMapper;
import school.sptech.menor_tempo_atendimento.repository.UpaRepository;

import java.util.List;

@Service
public class UpaService {

    @Autowired
    private UpaRepository upaRepository;

    public List<NoGrafo> getTempoEspera(List<String> upas){
        return NoGrafoMapper.toListNoGrafoTempoEspera(upaRepository.findByNomeIn(upas));
    }

}
