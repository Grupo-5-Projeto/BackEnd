package school.sptech.menor_tempo_atendimento.service.grafo;

import school.sptech.menor_tempo_atendimento.service.upa.UpaService;
import school.sptech.menor_tempo_atendimento.domain.Nivel;
import school.sptech.menor_tempo_atendimento.domain.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GrafoBuilder {
    private UpaService upaService;
    private List<NoGrafo> meioDeTransporteUpas;
    private HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa;

    public GrafoBuilder(List<NoGrafo> meioDeTransporteUpas, HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa
    , UpaService upaService) {
        this.meioDeTransporteUpas = meioDeTransporteUpas;
        this.valorArestaTransporteUpa = valorArestaTransporteUpa;
        this.upaService = upaService;
    }

    //Metodo para gerar o nos de maneira automatica
    //e nao precisar criando na mao
    //Paciente: Padrão -> ponto de inicio, não preciso de nenhuma info
    //MeioDeTransporte: Receber esses valores pela API do Maps
    //Upa: receber valores pela API do Maps (info de tempo do meio de transporte até a UPA)
    //tempo de espera: Receber valores pelo Banco de dados (info fornecida pela Visão computacional que nas UPAs)
    private Map<NoGrafo, List<Par<NoGrafo, Double>>> gerarNosGrafo() {
        Map<NoGrafo, List<Par<NoGrafo, Double>>> nosGrafo = new HashMap<>();

        NoGrafo paciente = new NoGrafo("paciente", Nivel.NIVEL_PACIENTE, 0);
        nosGrafo.putIfAbsent(paciente, new ArrayList<>());
        List<String> nomesUpas = new ArrayList<>();
        for (NoGrafo meioDeTransporte : meioDeTransporteUpas) {
            if (meioDeTransporte.getNivel() == Nivel.NIVEL_UPA) {
                nomesUpas.add(meioDeTransporte.getNome());
            }
        }
        for (NoGrafo meiosDeTranporteUpas : meioDeTransporteUpas)  nosGrafo.putIfAbsent(meiosDeTranporteUpas, new ArrayList<>());
        for (NoGrafo tempoDeEspera : upaService.getTempoEspera(nomesUpas)) nosGrafo.putIfAbsent(tempoDeEspera, new ArrayList<>());

        for (NoGrafo noDaVez: nosGrafo.keySet()){
            System.out.println(noDaVez.getNome());
        }
        return nosGrafo;
    }

    //Gerar as aresta do grafo de maneira automatica
    //para nao ter que criar na main na mao
    private Map<NoGrafo, List<Par<NoGrafo, Double>>> gerarArestasGrafo(Map<NoGrafo, List<Par<NoGrafo, Double>>> nosGrafo) {
        Map<NoGrafo, List<Par<NoGrafo, Double>>> adjacencia = new HashMap<>();
        NoGrafo paciente = null;

        for (NoGrafo no : nosGrafo.keySet()) {
            if ("paciente".equals(no.getNome())) {
                paciente = no;
                break;
            }
        }
        for (NoGrafo no : nosGrafo.keySet()) {
            if (no.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                adjacencia.get(paciente).add(new Par<>(no, (double) no.getTempo()));
                adjacencia.get(no).add(new Par<>(paciente, (double) no.getTempo()));
            }
            if (no.getNivel() == Nivel.NIVEL_UPA) {
                for (NoGrafo noDaVez : nosGrafo.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                        for (Par<String, Integer> tempoMeioDeTransporteUpa : valorArestaTransporteUpa.get(no.getNome())) {
                            if (tempoMeioDeTransporteUpa.getChave().equals(noDaVez.getNome())) {
                                adjacencia.get(no).add(new Par<>(noDaVez, (double) tempoMeioDeTransporteUpa.getValor()));
                                adjacencia.get(noDaVez).add(new Par<>(no, (double) tempoMeioDeTransporteUpa.getValor()));
                            }
                        }
                    }
                }
            }
            if (no.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo noDaVez : nosGrafo.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                        if (no.getNome().equals(noDaVez.getNome() + "-" + "tempoEspera")) {
                            adjacencia.get(no).add(new Par<>(noDaVez, (double) no.getTempo()));
                            adjacencia.get(noDaVez).add(new Par<>(no, (double) no.getTempo()));
                        }
                    }
                }
            }
        }
        return nosGrafo;
    }

    public Map<NoGrafo, List<Par<NoGrafo, Double>>> build(){
        return gerarArestasGrafo(gerarNosGrafo());
    }

}
