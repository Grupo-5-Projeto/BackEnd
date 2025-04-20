package school.sptech.menor_tempo_atendimento.mapper.grafo;



import school.sptech.menor_tempo_atendimento.util.Nivel;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Upa;

import java.util.ArrayList;
import java.util.List;

public class NoGrafoMapper {

    NoGrafo noGrafo = new NoGrafo();
    Upa upa = new Upa();

    public static List<NoGrafo> toListNoGrafoTempoEspera(List<Upa> upas) {
        List<NoGrafo> noGrafoList = new ArrayList<>();
        for(Upa upa: upas) {
            NoGrafo noGrafo = new NoGrafo();
            noGrafo.setNome(upa.getNome() + "-" + "tempoEspera");
            noGrafo.setTempo(upa.getTempoDeEspera());
            noGrafo.setNivel(Nivel.NIVEL_TEMPO_DE_ESPERA);
            noGrafoList.add(noGrafo);
        }
        return noGrafoList;
    }

}
