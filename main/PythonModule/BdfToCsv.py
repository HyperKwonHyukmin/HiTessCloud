from pyNastran.bdf.bdf import BDF
import pandas as pd
import sys


# 프로그램 작동 함수 main
def BdfToCsv(bdf_file):
  # BDF 파일 읽기
  # bdf_file = r"C:\Coding\Python\Projects\ModuleUnit\BDFtoCSV\BDF\3370_M04_csv.bdf"  # BDF 파일 경로를 입력하세요.
  model = BDF()
  model.read_bdf(bdf_file)

  csvText_list = []
  columns = ['name', 'type', 'pos', 'poss', 'pose', 'size', 'stru', 'ori', 'division', 'weld']
  isSupport = False

  # GRID 추출
  grid_dict = {}
  for grid_id, grid in model.nodes.items():
    grid_dict[int(grid_id)] = {
      'X': float(grid.xyz[0]),
      'Y': float(grid.xyz[1]),
      'Z': float(grid.xyz[2])
    }

  # CBEAM 추출
  cbeam_dict = {}
  for element_id, element in model.elements.items():
    if element.type == 'CBEAM':
      cbeam_dict[int(element_id)] = {
        'nodes': [int(element.node_ids[0]), int(element.node_ids[1])],
        'propertyID': int(element.pid)
      }

  # PBEAML 추출
  pbeaml_dict = {}
  for prop_id, prop in model.properties.items():
    if prop.type == 'PBEAML':
      pbeaml_dict[int(prop_id)] = {
        'materialID': int(prop.mid),
        'section_type': prop.Type
      }

  for cbeamID in cbeam_dict:
    if cbeam_dict[cbeamID]['propertyID'] == 1000:
      isSupport = True
      nodes = cbeam_dict[cbeamID]['nodes']
      nodeA = nodes[0]
      nodeB = nodes[1]
      poss = f'X {int(grid_dict[nodeA]["X"])}mm Y {int(grid_dict[nodeA]["Y"])}mm Z {int(grid_dict[nodeA]["Z"])}mm'
      pose = f'X {int(grid_dict[nodeB]["X"])}mm Y {int(grid_dict[nodeB]["Y"])}mm Z {int(grid_dict[nodeB]["Z"])}mm'
      csvText = [' =30137/384565', 'SCTN', poss, poss, pose, 'ANG_100x100x10', '0.0308360511306552',
                 '   0.000   0.000   1.000', 'SUPP', '']
      csvText_list.append(csvText)

  if not isSupport:  # id 1000 support가 없으면 프로그램 종료시켜 버리기
    sys.exit()

  csvText_df = pd.DataFrame(csvText_list)
  csvText_df.columns = columns

  csv_path = bdf_file.replace('.bdf', '.csv')
  print('csv_path : ', csv_path)
  csvText_df.to_csv(csv_path, index=False)

  return csv_path


if __name__ == "__main__":
  if len(sys.argv) > 1:
    print('sys.argv[1] : ', sys.argv[1])
    TempSupportExtract(sys.argv[1])  # 첫 번째 인자를 main 함수로 전달
  else:
    print("인자가 입력되지 않았습니다.")
    sys.exit()
