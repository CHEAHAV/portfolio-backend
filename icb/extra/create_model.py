from main import *
from icb.core.db import engine, db
from icb.core.model import Base
from sqlalchemy import text

class TableMigration(object):
  """docstring for CLS_Migration"""

  def alterAddColumn(self):
    # print 'Starting migration..........'
    sql = ''' SELECT * FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema'); '''
    AlterChangeLengthFieldSql = ''
    Module      =   __import__("main")

    # List all table in postgresql
    # print(db.execute(sql))
    for row in db.execute(text(sql)):
      AlterAddFieldSql = ''
      PostAlterSQL = ''
      TableName 	=	row[1]
      # print(TableName)
      if hasattr(Module,TableName.upper()):
        # if TableName[-5:] == '_EDIT':
        # 	AlterAddFieldSql += 'ALTER TABLE "%s" ALTER COLUMN "%s" %s PRIMARY KEY;'\
        # 					%(TableName,'CurrentNo','character varying(10)')

        PostgresFieldObjScript = ''' SELECT column_name, character_maximum_length,data_type,numeric_precision,numeric_scale,numeric_precision_radix,numeric_scale
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name   = '%s' '''%TableName
        TableLiveObj    =   getattr(Module, TableName.upper())
        PostgresFieldObj = db.execute(text(PostgresFieldObjScript))
        DicFieldInPostgres = {}

        # Add all column in table and length of field into dictionary	
        for PostField in PostgresFieldObj:
          DicFieldInPostgres.update({PostField[0]:{'length':PostField[1],'type':PostField[2], 'precision':PostField[3], 'scale':PostField[4]}})

        # List all variable in class model
        for c in TableLiveObj.__table__.columns:
          FieldName 		= 	c.name
          IsPrimaryKey 	=	c.primary_key
          IsAutoincrement =	c.autoincrement
          DefaultValue 	=	str(c.default).replace("ColumnDefault(",'').replace(")",'') if c.default and not 'Sequence' in str(c.default) else  "''"	
          FieldType 		= 	str(c.type).lower()			

          # check if field is not exist in table, meaning this is new field
          if DicFieldInPostgres.get(FieldName,'ISNULL')=='ISNULL':
                
            if 'integer' in FieldType or 'numeric' in FieldType:
              DefaultValue =	DefaultValue if DefaultValue != 0 else 0
              if type(DefaultValue) != int and type(DefaultValue) != float:
                DefaultValue = 0
            if FieldType in ['datetime','date']:
              SQLScript = 'ALTER TABLE "%s" ADD COLUMN "%s" %s;'%(TableName,FieldName,'date' if FieldType=='date' else 'timestamp')
              PostSQLScript=''
            elif FieldType == 'boolean':
              SQLScript = 'ALTER TABLE "%s" ADD COLUMN "%s" %s;'%(TableName,FieldName,'boolean')
              # PostSQLScript = 'UPDATE "%s" SET "%s"=%s WHERE "%s" IS NULL;'%(TableName,FieldName,DefaultValue,FieldName)
            else:
              SQLScript = 'ALTER TABLE "%s" ADD COLUMN "%s" %s;'%(TableName,FieldName,FieldType)
              # if IsPrimaryKey:
              # 	SQLScript = 'ALTER TABLE "%s" ADD COLUMN "%s" %s PRIMARY KEY;'\
              # 			%(TableName,FieldName,FieldType)
              # PostSQLScript = 'UPDATE "%s" SET "%s"=%s WHERE "%s" IS NULL;'\
              # 					%(TableName,FieldName,str(DefaultValue),FieldName)
            AlterAddFieldSql 	+= SQLScript
            # PostAlterSQL 		+= PostSQLScript
            print(PostAlterSQL)
            
          # this field is already exist and then check if length or type is different
          else:
            if FieldType in ['datetime','date']:
              DType = DicFieldInPostgres.get(FieldName,{}).get('type')
              if FieldType == 'datetime': FieldType = 'timestamp without time zone'
              if DType != FieldType:
                print(TableName,FieldName,FieldType,DType)
        
                if FieldType == 'date':
                  SQLScript =	'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE DATE using %s::DATE;'%(TableName,FieldName,FieldName)
                else:
                  SQLScript =	'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE TIMESTAMP using %s::TIMESTAMP;'%(TableName,FieldName,FieldName)
                AlterAddFieldSql += SQLScript
       
            if 'numeric' in FieldType:
              # print(TableName,FieldName,DicFieldInPostgres.get(FieldName), DicFieldInPostgres.get(FieldName).get('precision',28), DicFieldInPostgres.get(FieldName).get('scale',9))
              pre = DicFieldInPostgres.get(FieldName,{}).get('precision',28) if DicFieldInPostgres.get(FieldName,{}).get('precision',28) else 28
              scl = DicFieldInPostgres.get(FieldName,{}).get('scale',9) if DicFieldInPostgres.get(FieldName,{}).get('scale',9) else 9
              if int(c.type.precision if c.type.precision else 28)!=int(pre) or \
                int(c.type.scale if c.type.scale else 9)!=int(scl):
                SQLScript 	=	'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s using %s::numeric;'%(TableName,FieldName,FieldType,FieldName)
                AlterAddFieldSql += SQLScript

            if 'varchar' in FieldType: 
              FieldLength = DicFieldInPostgres.get(FieldName).get('length')
              try:
                # print(FieldName,FieldLength,c.type.length)
                # if int(FieldLength)<int(c.type.length):
                if FieldLength!=c.type.length:
                  SQLScript 	=	'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s;'%(TableName,FieldName,FieldType)
                  AlterAddFieldSql += SQLScript
                  print(AlterAddFieldSql)
              except Exception as e:
                print(e)
                pass
              
            if 'text' in FieldType: 
              FieldLength = DicFieldInPostgres.get(FieldName).get('length')
              try:
                if FieldLength!=c.type.length:
                  SQLScript 	=	'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s;'%(TableName,FieldName,FieldType)
                  AlterAddFieldSql += SQLScript
                  print(AlterAddFieldSql)
              except Exception as e:
                print(e)
                pass
            if FieldType == 'boolean':
              DType = DicFieldInPostgres.get(FieldName,{}).get('type')
              
              if DType != FieldType:
                SQLScript = '''ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s USING 
                                CASE 
                                    WHEN LOWER(%s) IN ('true', 't', 'yes', 'y', '1') THEN TRUE
                                    WHEN LOWER(%s) IN ('false', 'f', 'no', 'n', '0') THEN FALSE
                                    ELSE FALSE
                                END;'''%(TableName,FieldName,FieldType,FieldName,FieldName)
                AlterAddFieldSql += SQLScript
       
            if FieldType == 'integer':
              DType = DicFieldInPostgres.get(FieldName,{}).get('type')
              
              if DType != FieldType:
                SQLScript = 'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s using "%s"::integer;'%(TableName,FieldName,FieldType,FieldName)
                AlterAddFieldSql += SQLScript
            
            if FieldType in ['json','jsonb']:
              DType = DicFieldInPostgres.get(FieldName,{}).get('type')
              
              if DType != FieldType:
                SQLScript = 'ALTER TABLE "%s" ALTER COLUMN "%s" TYPE %s using "%s"::%s;'%(TableName,FieldName,FieldType,FieldName,FieldType)
                AlterAddFieldSql += SQLScript
            
    
      if AlterAddFieldSql or PostAlterSQL:
        try:
          if AlterAddFieldSql:
            print('AlterAddFieldSql',AlterAddFieldSql)
            db.execute(text(AlterAddFieldSql))
            db.commit()

          if PostAlterSQL:
            try:
              print('PostAlterSQL',PostAlterSQL)
              db.execute(text(PostAlterSQL))
              db.commit()
            except Exception as e:
              raise e
        except Exception as e:
          raise e

  def execute(self):
    print('\nStarting Alter Table...!')
    self.alterAddColumn()

    print('Finished Alter Table 100%')
      



if __name__ == "__main__":
  # Base.metadata.drop_all(bind=engine)
  Base.metadata.create_all(bind=engine)
  TableMigration().execute()