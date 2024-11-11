import React, { useRef } from 'react';
import Handsontable from 'handsontable';
import { HotTable } from '@handsontable/react';
import 'handsontable/dist/handsontable.full.min.css';

const MainTest: React.FC = () => {
    const data = [
        ['00934', 'DIN 934 Nakrętka sześciokątna'],
        ['00985', 'DIN 985 Nakrętka sześciokątna Samohamowna'],
        ['00982', 'DIN 982 Nakrętka sześciokątna Samohamowna'],
    ];

    return (
        <div className="MainTest">
            <h1>Test Table with Handsontable</h1>
            <HotTable
                data={data}
                colHeaders={['Numery dla segmentu', 'Nazwa dla numeru']} // Tytuły kolumn
                rowHeaders={true} // Nagłówki wierszy
                width="600"
                height="300"
                stretchH="all" // Rozciąganie kolumn na całą szerokość
                licenseKey="non-commercial-and-evaluation" // Darmowa licencja
                contextMenu={true} // Menu kontekstowe (klik prawym przyciskiem myszy)
                manualRowResize={true} // Możliwość zmiany rozmiaru wierszy
                manualColumnResize={true} // Możliwość zmiany rozmiaru kolumn
                copyPaste={true} // Kopiowanie i wklejanie
                allowInsertRow={true} // Zezwalaj na dodawanie nowych wierszy
                allowInsertColumn={true} // Zezwalaj na dodawanie nowych kolumn
                allowRemoveRow={true} // Zezwalaj na usuwanie wierszy
                readOnly={false} // Możliwość edytowania tabeli
                undo={true} // Funkcja cofania
                redo={true} // Funkcja ponawiania
                colWidths={150} // Ustawienie szerokości kolumn
                minCols={2} // Minimalna liczba kolumn
                maxCols={2} // Maksymalna liczba kolumn
                minRows={3} // Minimalna liczba wierszy
                autoColumnSize={true} // Automatyczne dopasowanie szerokości kolumn
                autoRowSize={true} // Automatyczne dopasowanie wysokości wierszy

                minSpareRows={1} // Dodanie jednego pustego wiersza na końcu tabeli
            />
        </div>
    );
};

export default MainTest;