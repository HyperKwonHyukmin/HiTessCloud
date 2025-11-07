import numpy as np


## Nodes 클래스 ########################################################################################################

class Nodes:
  def __init__(self):
    self.nodes = {}


  def GetMaxID(self):  # 최대 Node ID 반환 (새로운 Node 생성 시 사용)
    maxNodeID = max(self.nodes.keys())
    return maxNodeID


  def AddOrGet(self, x, y, z):
    # 클래스 자체에 데이터를 추가 또는 가져오기를 할 때 사용하는 메써드
    maxNodeID = self.GetMaxID()
    # x, y, z가 모두 실수인지 확인
    if not all(isinstance(coord, (float, int)) for coord in [x, y, z]):
      raise TypeError("Coordinates x, y, z must be integers or floats.")

    # 동일한 노드가 있는지 확인하고 있으면 해당 ID 반환, 없으면 새로 추가
    for node_id, coords in self.nodes.items():
      if coords == {'X': x, 'Y': y, 'Z': z}:
        return node_id
    maxNodeID += 1
    self.nodes[maxNodeID] = {'X': x, 'Y': y, 'Z': z}
    return maxNodeID


  def ImportFromBDF(self, nodeID, x, y, z):
    # bdf에서 Node, element 등의 모델링 정보를 클래스로 변환할때 사용하는 메써드
    self.nodes[nodeID] = {'X': x, 'Y': y, 'Z': z}


  def Remove(self, nodeID):
    # 주어진 ID의 노드를 제거
    if nodeID in self.nodes:
      del self.nodes[nodeID]


  def GetInfo(self, nodeID):
    # 주어진 ID의 노드 정보를 반환
    return self.nodes.get(nodeID, None)


  def __len__(self):
    # 노드의 총 개수 반환
    return len(self.nodes)


  def __iter__(self):
    # 노드들을 순회할 수 있는 이터레이터 제공
    return iter(self.nodes.items())


  def __getitem__(self, nodeID):
    # 주어진 ID의 노드 정보를 조회하는 매직 메서드
    return self.GetInfo(nodeID)


  def __setitem__(self, nodeID, coordinates):
    # 주어진 ID의 노드 데이터를 업데이트
    if nodeID in self.nodes:
      x, y, z = coordinates
      self.nodes[nodeID] = {'X': x, 'Y': y, 'Z': z}
    else:
      raise KeyError(f"Node ID {nodeID} does not exist.")  # 존재하지 않는 Node의 __setitem__ 사용을 막는다.


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    nodes_repr = ", ".join([f"{nodeID}: {nodeValue}" for nodeID, nodeValue in self.nodes.items()])
    return f"Nodes (Total: {len(self.nodes)}): {nodes_repr}"


## Element 클래스 ######################################################################################################
class Elements:
  def __init__(self, node_cls, property_cls):
    self.elements = {}
    self.node_cls = node_cls
    self.property_cls = property_cls


  def GetMaxID(self):  # 최대 Node ID 반환 (새로운 Node 생성 시 사용)
    maxElementID = max(self.elements.keys())
    return maxElementID


  def AddOrGet(self, node_ids, propertyID, rest=None):
    maxElementID = self.GetMaxID()
    # 동일한 요소가 있는지 확인하고 있으면 해당 ID 반환, 없으면 새로 추가
    for element_id, element_info in self.elements.items():
      if element_info['nodes'] == node_ids and element_info[
        'property'] == propertyID and element_info['rest'] == rest:
        return element_id
    maxElementID += 1
    self.elements[maxElementID] = {'nodes': node_ids, 'property': propertyID,
                                   'orientation': self.CalcOrientation(node_ids[0], node_ids[1]), 'rest': rest}
    return maxElementID


  def ImportFromBDF(self, elementID, node_ids, propertyID, orientation, rest=None):
    self.elements[elementID] = {'nodes': node_ids, 'property': propertyID,
                                'orientation': orientation, 'rest': rest}


  def Remove(self, elementID):
    # 주어진 ID의 요소를 제거
    if elementID in self.elements:
      del self.elements[elementID]


  def GetInfo(self, elementID):
    # 주어진 ID의 요소 정보를 반환
    element_info = self.elements.get(elementID, None)
    if element_info:
      node_coordinates = [self.node_cls.GetInfo(node_id) for node_id in element_info['nodes']]
      element_info['node_coordinates'] = node_coordinates
    return element_info


  def CalcOrientation(self, nodeA, nodeB):
    '''
    하나의 element를 이루는 두 Node가 X 또는 Y 또는 Z축에 평행한지 확인
    '''
    nodeALoca = self.node_cls.GetInfo(nodeA)
    nodeBLoca = self.node_cls.GetInfo(nodeB)
    # print(nodeALoca)
    # print(nodeBLoca)

    # 노드의 좌표 차이 계산
    delta = {axis: nodeBLoca[axis] - nodeALoca[axis] for axis in ['X', 'Y', 'Z']}

    # 각 축에 평행한지 확인
    parallel_to_x = (delta['X'] != 0 and delta['Y'] == 0 and delta['Z'] == 0)
    parallel_to_y = (delta['X'] == 0 and delta['Y'] != 0 and delta['Z'] == 0)
    parallel_to_z = (delta['X'] == 0 and delta['Y'] == 0 and delta['Z'] != 0)
    parallel_to_xy = (delta['X'] != 0 and delta['Y'] != 0 and delta['Z'] == 0)
    parallel_to_yz = (delta['X'] == 0 and delta['Y'] != 0 and delta['Z'] != 0)
    parallel_to_zx = (delta['X'] != 0 and delta['Y'] == 0 and delta['Z'] != 0)

    if parallel_to_x:
      return [0.0, 0.0, 1.0]
    elif parallel_to_y:
      return [0.0, 0.0, 1.0]
    elif parallel_to_z:
      return [1.0, 0.0, 0.0]
    elif parallel_to_xy:
      return [0.0, 0.0, 1.0]
    elif parallel_to_yz:
      return [0.0, 0.0, 1.0]
    elif parallel_to_zx:
      return [0.0, 0.0, 1.0]
    else:
      return [0.0, 0.0, 1.0]  # Default orientation


  def __len__(self):
    # 요소의 총 개수 반환
    return len(self.elements)


  def __iter__(self):
    # 요소들을 순회할 수 있는 이터레이터 제공
    return iter(self.elements.items())


  def __getitem__(self, elementID):
    # 주어진 ID의 요소 정보를 조회하는 매직 메서드
    return self.GetInfo(elementID)


  def __setitem__(self, elementID, element_data):
    # 주어진 ID의 요소 데이터를 업데이트
    if elementID in self.elements:
      node_ids, propertyID = element_data
      self.elements[elementID] = {'nodes': node_ids, 'property': propertyID,
                                  'orientation': self.CalcOrientation(node_ids[0], node_ids[1])}
    else:
      raise KeyError(f"Element ID {elementID} does not exist.")


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    elements_repr = ", ".join([f"{elementID}: {data}" for elementID, data in self.elements.items()])
    return f"Elements (Total: {len(self.elements)}): {elements_repr}"


# Properties 클래스 ####################################################################################################
class Properties:
  def __init__(self, material_cls):
    self.properties = {}
    self.material_cls = material_cls


  def GetMaxID(self):  # 최대 Node ID 반환 (새로운 Node 생성 시 사용)
    maxPropertyID = max(self.properties.keys())
    return maxPropertyID


  def AddOrGet(self, type, materialID, dim, rest=None):
    maxPropertyID = self.GetMaxID()
    for prop_id, prop_info in self.properties.items():
      if prop_info['type'] == type and prop_info['material'] == materialID and prop_info['dim'] == dim and prop_info[
        'rest'] == rest:
        return prop_id

    # 새로운 속성 추가
    maxPropertyID += 1
    self.properties[maxPropertyID] = {'type': type, 'material': materialID, 'dim': dim, 'rest': rest}
    return maxPropertyID


  def ImportFromBDF(self, propertyID, type, materialID, dim, rest=None):
    self.properties[propertyID] = {'type': type, 'material': materialID, 'dim': dim, 'rest': rest}


  def GetInfo(self, propertyID):
    # 주어진 ID의 속성 정보를 반환
    return self.properties.get(propertyID, None)


  def __getitem__(self, propertyID):
    # 주어진 ID의 속성 정보를 조회하는 매직 메서드
    return self.GetInfo(propertyID)


  def __setitem__(self, propertyID, property_data):
    # 주어진 ID의 속성 데이터를 업데이트
    if propertyID in self.properties:
      type, materialID, dim = property_data
      self.properties[propertyID] = {'type': type, 'material': materialID, 'dim': dim}
    else:
      raise KeyError(f"Property ID {propertyID} does not exist.")


  def __iter__(self):
    # 속성들을 순회할 수 있는 이터레이터 제공
    return iter(self.properties.items())


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    properties_repr = ", ".join([f"{propertyID}: {data}" for propertyID, data in self.properties.items()])
    return f"Properties (Total: {len(self.properties)}): {properties_repr}"


# Materials 클래스 #####################################################################################################
class Materials:
  def __init__(self):
    self.materials = {}


  def GetMaxID(self):  # 최대 Node ID 반환 (새로운 Node 생성 시 사용)
    maxMaterialID = max(self.materials.keys())
    return maxMaterialID


  def AddOrGet(self, E, nu, rho, rest=None):
    maxMaterialID = self.GetMaxID()
    # 동일한 재료가 있는지 확인하고 있으면 해당 ID 반환, 없으면 새로 추가
    for material_id, material_info in self.materials.items():
      if material_info == {'E': E, 'nu': nu, 'rho': rho, 'rest': rest}:
        return material_id
    maxMaterialID += 1
    self.materials[maxMaterialID] = {'E': E, 'nu': nu, 'rho': rho, 'rest': rest}
    return maxMaterialID


  def ImportFromBDF(self, materialID, E, nu, rho, rest=None):
    self.materials[materialID] = {'E': E, 'nu': nu, 'rho': rho, 'rest': rest}


  def GetInfo(self, materialID):
    # 주어진 ID의 재료 정보를 반환
    return self.materials.get(materialID, None)


  def __getitem__(self, materialID):
    # 주어진 ID의 재료 정보를 조회하는 매직 메서드
    return self.GetInfo(materialID)


  def __setitem__(self, materialID, material_info):
    # 주어진 ID의 재료 데이터를 업데이트
    if materialID in self.materials:
      self.materials[materialID] = material_info
    else:
      raise KeyError(f"Material ID {materialID} does not exist.")


  def __iter__(self):
    # 재료들을 순회할 수 있는 이터레이터 제공
    return iter(self.materials.items())


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    materials_repr = ", ".join([f"{materialID}: {data}" for materialID, data in self.materials.items()])
    return f"Materials (Total: {len(self.materials)}): {materials_repr}"


## Comn 클래스 ######################################################################################################
class Comn:
  def __init__(self):
    self.comn = {}


  def GetMaxID(self):
    if not self.comn:
      return 0
    return max(self.comn.keys())


  def ImportFromBDF(self, comnID, nodeID, massValue):
    self.comn[comnID] = {"NodesID": nodeID, "Mass": massValue}


  def GetInfo(self, mass_id):
    # 주어진 ID의 질량 정보를 반환
    return self.comn.get(mass_id, None)


  def __getitem__(self, mass_id):
    # 주어진 ID의 질량 정보를 조회하는 매직 메서드
    return self.GetInfo(mass_id)


  def __setitem__(self, mass_id, mass_data):
    # 주어진 ID의 질량 데이터를 업데이트
    node_id, mass_value = mass_data
    self.AddMass(mass_id, node_id, mass_value)
    if mass_id in self.comn:
      self.comn[mass_id] = mass_data


  def __iter__(self):
    # 질량 정보를 순회할 수 있는 이터레이터 제공
    return iter(self.comn.items())


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    comn_repr = ", ".join([f"{mass_id}: {data}" for mass_id, data in self.comn.items()])
    return f"Comn (Total: {len(self.comn)}): {comn_repr}"

## Rigid 클래스 ######################################################################################################
class Rigid:
  def __init__(self):
    self.rigid = {}

  def ImportFromBDF(self, rigidID, independent_node, dependent_nodes, dof):
    self.rigid[rigidID] = {"ind_node": independent_node, "dep_nodes": dependent_nodes, "DOF" : dof}


  def GetInfo(self, rigid_id):
    # 주어진 ID의 강체 요소 정보를 반환
    return self.rigid.get(rigid_id, "Rigid element not found.")


  def __getitem__(self, rigid_id):
    # 주어진 ID의 강체 요소 정보를 조회하는 매직 메서드
    return self.GetInfo(rigid_id)

  def __iter__(self):
    # 질량 정보를 순회할 수 있는 이터레이터 제공
    return iter(self.rigid.items())


  def __repr__(self):
    # 클래스의 문자열 표현 제공
    rigid_repr = ", ".join([f"{rigid_id}: {data}" for rigid_id, data in self.rigid.items()])
    return f"RigidElements (Total: {len(self.rigid)}): {rigid_repr}"
